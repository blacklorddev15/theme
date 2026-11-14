import React, { forwardRef } from 'react';
import { Form } from 'formik';
import styled from 'styled-components/macro';
import { breakpoint } from '@/theme';
import FlashMessageRender from '@/components/FlashMessageRender';
import tw from 'twin.macro';

type Props = React.DetailedHTMLProps<React.FormHTMLAttributes<HTMLFormElement>, HTMLFormElement> & {
    title?: string;
    variant?: 'default' | 'luxury';
};

const Container = styled.div`
    ${breakpoint('sm')`
        ${tw`w-4/5 mx-auto`}
    `};
    ${breakpoint('md')`
        ${tw`p-10`}
    `};
    ${breakpoint('lg')`
        ${tw`w-3/5`}
    `};
    ${breakpoint('xl')`
        ${tw`w-full`}
        max-width: 700px;
    `};
`;

const LuxuryPage = styled.div`
    position: fixed;
    z-index: 100;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow-y: auto;
    padding: 32px 20px;
    isolation: isolate;
    color: #f4f7f4;
    background: radial-gradient(ellipse at 50% 0%, rgba(39, 106, 72, 0.32), transparent 42%),
        radial-gradient(ellipse at 8% 78%, rgba(28, 84, 58, 0.2), transparent 34%),
        radial-gradient(ellipse at 100% 100%, rgba(20, 58, 42, 0.2), transparent 38%),
        linear-gradient(145deg, #050907 0%, #08120d 52%, #030605 100%);

    &::before {
        content: '';
        position: absolute;
        z-index: -1;
        inset: 0;
        pointer-events: none;
        opacity: 0.12;
        background-image: linear-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.12) 1px, transparent 1px);
        background-size: 56px 56px;
        mask-image: radial-gradient(ellipse at center, #000 0%, transparent 80%);
    }

    @media (max-width: 480px) {
        padding: 18px 14px;
    }
`;

const LuxuryCard = styled.div`
    width: 100%;
    max-width: 448px;
    margin: auto;
    padding: 38px 38px 25px;
    border: 1px solid rgba(221, 246, 230, 0.13);
    border-radius: 25px;
    background: linear-gradient(150deg, rgba(255, 255, 255, 0.085), rgba(255, 255, 255, 0.035));
    box-shadow: 0 28px 90px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(22px);
    -webkit-backdrop-filter: blur(22px);

    .login-eyebrow {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 9px;
        margin-bottom: 21px;
        color: rgba(202, 222, 209, 0.66);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
    }

    .login-eyebrow-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #6db68a;
        box-shadow: 0 0 14px rgba(109, 182, 138, 0.72);
    }

    .login-title {
        margin: 0;
        color: rgba(247, 250, 247, 0.78);
        font-family: Georgia, 'Times New Roman', serif;
        font-size: clamp(30px, 7vw, 36px);
        font-style: italic;
        font-weight: 300;
        line-height: 1.15;
        text-align: center;
    }

    .login-title strong {
        color: #fff;
        font-style: normal;
        font-weight: 700;
    }

    .login-subtitle {
        margin: 11px 0 0;
        color: rgba(226, 235, 229, 0.57);
        font-size: 14px;
        line-height: 1.55;
        text-align: center;
    }

    .login-luxe-form {
        display: block;
        width: 100%;
        margin-top: 28px;
    }

    .login-form-fields {
        display: flex;
        flex-direction: column;
        gap: 18px;
        width: 100%;
    }

    .login-form-fields > * {
        margin-top: 0 !important;
    }

    .login-field-wrap {
        position: relative;
        width: 100%;
    }

    .login-luxe-form label {
        display: block;
        margin: 0 0 8px;
        color: rgba(217, 231, 221, 0.72);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.12em;
    }

    .login-luxe-form .login-input {
        display: block;
        width: 100%;
        min-height: 54px;
        padding: 14px 46px;
        border: 1px solid rgba(226, 243, 232, 0.13);
        border-radius: 15px;
        outline: none;
        background: rgba(255, 255, 255, 0.055);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.025);
        color: #f7faf7;
        font-size: 14px;
        transition: border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
    }

    .login-luxe-form .login-input::placeholder {
        color: rgba(226, 235, 229, 0.36);
    }

    .login-luxe-form .login-input:hover:not(:disabled) {
        border-color: rgba(226, 243, 232, 0.24);
        background: rgba(255, 255, 255, 0.075);
    }

    .login-luxe-form .login-input:focus:not(:disabled) {
        border-color: rgba(116, 184, 143, 0.74);
        background: rgba(255, 255, 255, 0.075);
        box-shadow: 0 0 0 3px rgba(73, 138, 99, 0.17);
    }

    .login-field-icon {
        position: absolute;
        z-index: 1;
        top: 47px;
        left: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(202, 222, 209, 0.62);
        pointer-events: none;
        transform: translateY(-50%);
    }

    .login-password-toggle {
        position: absolute;
        z-index: 2;
        top: 47px;
        right: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        padding: 0;
        border: 0;
        border-radius: 8px;
        background: transparent;
        color: rgba(202, 222, 209, 0.7);
        cursor: pointer;
        transform: translateY(-50%);
    }

    .login-password-toggle:hover,
    .login-password-toggle:focus-visible {
        outline: none;
        background: rgba(255, 255, 255, 0.08);
        color: #fff;
    }

    .login-luxe-form .input-help {
        margin: 6px 1px 0;
        color: #f7b5ad;
        font-size: 12px;
        line-height: 1.4;
    }

    .login-luxe-form .input-help.error {
        color: #f7b5ad;
    }

    .login-luxe-form button[type='submit'] {
        width: 100%;
        min-height: 54px;
        margin-top: 3px;
        padding: 13px 18px;
        border: 1px solid rgba(164, 215, 182, 0.26);
        border-radius: 15px;
        background: linear-gradient(135deg, #3f7959 0%, #2e6247 100%);
        box-shadow: 0 10px 25px rgba(17, 68, 42, 0.27), inset 0 1px 0 rgba(255, 255, 255, 0.13);
        color: #fff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.15em;
        transition: transform 150ms ease, filter 150ms ease, box-shadow 150ms ease;
    }

    .login-luxe-form button[type='submit']:hover:not(:disabled) {
        border-color: rgba(181, 227, 197, 0.44);
        background: linear-gradient(135deg, #4a8965 0%, #377552 100%);
        box-shadow: 0 12px 28px rgba(17, 68, 42, 0.36), inset 0 1px 0 rgba(255, 255, 255, 0.16);
        transform: translateY(-1px);
    }

    .login-luxe-form button[type='submit']:disabled {
        cursor: wait;
        opacity: 0.66;
    }

    .login-luxe-form .login-forgot {
        margin-top: 2px;
        text-align: right;
    }

    .login-luxe-form .login-forgot a {
        color: rgba(196, 219, 203, 0.67);
        font-size: 12px;
        text-decoration: none;
        transition: color 150ms ease;
    }

    .login-luxe-form .login-forgot a:hover,
    .login-luxe-form .login-forgot a:focus-visible {
        color: #fff;
        outline: none;
    }

    .login-footer {
        margin: 26px 0 0;
        padding-top: 17px;
        border-top: 1px solid rgba(255, 255, 255, 0.075);
        color: rgba(226, 235, 229, 0.34);
        font-size: 10px;
        letter-spacing: 0.05em;
        text-align: center;
    }

    .login-footer a {
        color: inherit;
        text-decoration: none;
    }

    .login-footer a:hover {
        color: rgba(226, 235, 229, 0.7);
    }

    @media (max-width: 480px) {
        padding: 31px 23px 22px;
        border-radius: 21px;

        .login-luxe-form {
            margin-top: 24px;
        }
    }
`;

export default forwardRef<HTMLFormElement, Props>(({ title, variant = 'default', ...props }, ref) => {
    if (variant === 'luxury') {
        return (
            <LuxuryPage>
                <LuxuryCard>
                    <div className={'login-eyebrow'}>
                        <span className={'login-eyebrow-dot'} />
                        Secure panel access
                    </div>
                    <h2 className={'login-title'}>
                        Welcome <strong>Back!</strong>
                    </h2>
                    <p className={'login-subtitle'}>Sign in to continue to your server panel.</p>
                    <FlashMessageRender css={tw`mt-5`} />
                    <Form {...props} ref={ref} className={'login-luxe-form'}>
                        <div className={'login-form-fields'}>{props.children}</div>
                    </Form>
                    <p className={'login-footer'}>
                        &copy; 2015 - {new Date().getFullYear()}&nbsp;
                        <a rel={'noopener nofollow noreferrer'} href={'https://pterodactyl.io'} target={'_blank'}>
                            Pterodactyl Software
                        </a>
                    </p>
                </LuxuryCard>
            </LuxuryPage>
        );
    }

    return (
        <Container>
            {title && <h2 css={tw`text-3xl text-center text-neutral-100 font-medium py-4`}>{title}</h2>}
            <FlashMessageRender css={tw`mb-2 px-1`} />
            <Form {...props} ref={ref}>
                <div css={tw`md:flex w-full bg-white shadow-lg rounded-lg p-6 md:pl-0 mx-1`}>
                    <div css={tw`flex-none select-none mb-6 md:mb-0 self-center`}>
                        <img src={'/assets/svgs/pterodactyl.svg'} css={tw`block w-48 md:w-64 mx-auto`} />
                    </div>
                    <div css={tw`flex-1`}>{props.children}</div>
                </div>
            </Form>
            <p css={tw`text-center text-neutral-500 text-xs mt-4`}>
                &copy; 2015 - {new Date().getFullYear()}&nbsp;
                <a
                    rel={'noopener nofollow noreferrer'}
                    href={'https://pterodactyl.io'}
                    target={'_blank'}
                    css={tw`no-underline text-neutral-500 hover:text-neutral-300`}
                >
                    Pterodactyl Software
                </a>
            </p>
        </Container>
    );
});
